#!/usr/bin/env python
# TODO:
#   - need support for overwriting existing templates on S3
#   - argparse functionality for picking functions
#   - add a check to see if stack exists prior to uploading the template

from __future__ import print_function
from boto import (cloudformation, s3, exception)
import argparse
import time
import sys

class Stacker():
    def __init__(self, region):
        self.region = region
        self.cf = cloudformation.connect_to_region(self.region)

    def list_stacks(self):
        self.successful_filter = ["UPDATE_COMPLETE", "CREATE_COMPLETE"]
        self.failed_filter = ["CREATE_FAILED", "UPDATE_ROLLBACK_FAILED",
                              "DELETE_FAILED", "ROLLBACK_FAILED",
                              "ROLLBACK_IN_PROGRESS", "ROLLBACK_COMPLETE",
                              "UPDATE_ROLLBACK_COMPLETE"]
        self.update_filter = ["UPDATE_ROLLBACK_FAILED",
                              "UPDATE_ROLLBACK_IN_PROGRESS",
                              "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS",
                              "UPDATE_COMPLETE","UPDATE_IN_PROGRESS",
                              "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS",
                              "UPDATE_ROLLBACK_COMPLETE"]

        successful_stacks = self.cf.list_stacks(stack_status_filters=self.successful_filter)
        failed_stacks = self.cf.list_stacks(stack_status_filters=self.failed_filter)
        update_stacks = self.cf.list_stacks(stack_status_filters=self.update_filter)

        print("Successful CloudFormation Stacks:")
        for stack in successful_stacks:
            print(stack.stack_name)

        print("Failed CloudFormation Stacks:")
        for stack in failed_stacks:
            print(stack.stack_name)

        print("Update CloudFormation Stacks:")
        for stack in update_stacks:
            print(stack.stack_name)

    def upload_template(self, local_template):
        '''
        Upload template file to S3 bucket to be parsed by the CF create function.

        :param str self.bucket              S3 bucket name
        :param str self.local_template      local template file
        :param str self.template            template name without the path
        '''
        self.bucket = 'cf-templates-158gc87u1eu1y-us-east-1'
        self.local_template = local_template
        self.template = self.local_template.replace('/home/mike/', '')

        print("Uploading new template file to s3")
        self.conn = s3.connect_to_region('us-east-1')
        try:
            b = self.conn.get_bucket(self.bucket)
            k = s3.key.Key(b)
            k.key = self.template
            k.set_contents_from_filename(self.local_template, replace=True)
            #k.close
        except:
            print("Failed uploading the new template to s3")
        finally:
            template_url = "http://s3.amazonaws.com/" + self.bucket + "/" + self.template
        return template_url

    def local_template(self, local_template):
        '''
        Return template body from a template file.

        :param str self.local_template      template file location
        :param str self.template            template body object
        '''
        self.local_template = local_template
        self.template = template

        with open(self.local_template, 'r') as f:
            self.template = f.readline()
        f.close
        return self.template

    def stack_status(self, stack_name):
        self.stack_name = stack_name

        print("Getting stack status...")
        while True:
            time.sleep(15)
            try:
                self.status = self.cf.describe_stack_events(stack_name_or_id=self.stack_name)
            finally:
                self.status.reverse()
                if "Stack " + self.stack_name + " CREATE_COMPLETE" in str(self.status):
                    print("Creation of stack " + self.stack_name + " complete.")
                    break
                elif "Stack " + self.stack_name + "DELETE_IN_PROGRESS" in str(self.status):
                    print("Deletion of stack " + self.stack_name + " in progress.")
                    break

    def create_stack(self, stack_name, template):
        self.stack_name = stack_name
        self.template = template
        try:
            print("Creating a new stack using template: " + self.template)
            self.cf.create_stack(self.stack_name, template_url=self.template)
            self.stack_status(self.stack_name)
        except exception.BotoServerError as e:
            print("Failed creating stack using template: " + self.template)
            print(e)

    def delete_stack(self, stack_name):
        self.stack_name = stack_name
        try:
            print("Deleteing stack " + self.stack_name)
            self.cf.delete_stack(stack_name_or_id=self.stack_name)
            self.stack_status(self.stack_name)
        except exception.BotoServerError as e:
            print("Failed deleting stack : " + self.template)
            print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AWS CloudFormation CLI tool")
    parser.add_argument('-c', '--create', action='store_true', dest='create', help="Create stack using a template")
    parser.add_argument('-d', '--delete', action='store_true', dest='delete', help="Delete a given stack")
    parser.add_argument('-l', '--list', action='store_true', dest='list', help="List existing stacks")
    parser.add_argument('-t', '--template', action='store', dest='template_file', nargs='*', help="Location of the template file")
    parser.add_argument('-s', '--stack', action='store', dest='stack_name', nargs='*', help="Stack name")
    results = parser.parse_args()

    if not vars(results):
        parser.print_help()
        sys.exit(0)

    s = Stacker('us-east-1')
    if results.list:
        stacks = s.list_stacks()
        print(stacks)
    elif results.create:
        if results.template_file:
            template_url = s.upload_(template(results.template_file))
            stacks = s.create_stack(results.stack_name, template_url)
        elif results.template_url:
            stacks = s.create_stack(results.stack_name, template_url)
    elif results.delete:
        stacks = s.delete_stack(results.stack_name)
    else:
        parser.print_help()

    # upload local file to s3 bucket and then reference the file via s3 web url
    #template = "https://s3.amazonaws.com/cf-templates-158gc87u1eu1y-us-east-1/ec2_goatherding_us-east.yaml"
    #template_url = s.upload_template('/home/mike/ec2_goatherding_us-east.yaml')
    #print(template_url)
    #s.create_stack("test3", template_url)
